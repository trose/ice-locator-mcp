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
import {
  CreateCloudFrontOriginAccessIdentityRequest,
  CreateCloudFrontOriginAccessIdentityResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateCloudFrontOriginAccessIdentityCommandInput
  extends CreateCloudFrontOriginAccessIdentityRequest {}
export interface CreateCloudFrontOriginAccessIdentityCommandOutput
  extends CreateCloudFrontOriginAccessIdentityResult,
    __MetadataBearer {}
export declare class CreateCloudFrontOriginAccessIdentityCommand extends $Command<
  CreateCloudFrontOriginAccessIdentityCommandInput,
  CreateCloudFrontOriginAccessIdentityCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateCloudFrontOriginAccessIdentityCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateCloudFrontOriginAccessIdentityCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateCloudFrontOriginAccessIdentityCommandInput,
    CreateCloudFrontOriginAccessIdentityCommandOutput
  >;
  private serialize;
  private deserialize;
}
