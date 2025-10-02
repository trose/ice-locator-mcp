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
import { DeleteResponseHeadersPolicyRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteResponseHeadersPolicyCommandInput
  extends DeleteResponseHeadersPolicyRequest {}
export interface DeleteResponseHeadersPolicyCommandOutput
  extends __MetadataBearer {}
export declare class DeleteResponseHeadersPolicyCommand extends $Command<
  DeleteResponseHeadersPolicyCommandInput,
  DeleteResponseHeadersPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteResponseHeadersPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteResponseHeadersPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteResponseHeadersPolicyCommandInput,
    DeleteResponseHeadersPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
