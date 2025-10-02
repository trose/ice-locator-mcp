import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { DeleteCloudFrontOriginAccessIdentityRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteCloudFrontOriginAccessIdentityCommandInput
  extends DeleteCloudFrontOriginAccessIdentityRequest {}
export interface DeleteCloudFrontOriginAccessIdentityCommandOutput
  extends __MetadataBearer {}
export declare class DeleteCloudFrontOriginAccessIdentityCommand extends $Command<
  DeleteCloudFrontOriginAccessIdentityCommandInput,
  DeleteCloudFrontOriginAccessIdentityCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteCloudFrontOriginAccessIdentityCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteCloudFrontOriginAccessIdentityCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteCloudFrontOriginAccessIdentityCommandInput,
    DeleteCloudFrontOriginAccessIdentityCommandOutput
  >;
  private serialize;
  private deserialize;
}
