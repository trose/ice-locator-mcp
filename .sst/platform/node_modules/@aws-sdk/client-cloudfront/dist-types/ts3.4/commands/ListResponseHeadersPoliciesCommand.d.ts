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
  ListResponseHeadersPoliciesRequest,
  ListResponseHeadersPoliciesResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListResponseHeadersPoliciesCommandInput
  extends ListResponseHeadersPoliciesRequest {}
export interface ListResponseHeadersPoliciesCommandOutput
  extends ListResponseHeadersPoliciesResult,
    __MetadataBearer {}
export declare class ListResponseHeadersPoliciesCommand extends $Command<
  ListResponseHeadersPoliciesCommandInput,
  ListResponseHeadersPoliciesCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListResponseHeadersPoliciesCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListResponseHeadersPoliciesCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListResponseHeadersPoliciesCommandInput,
    ListResponseHeadersPoliciesCommandOutput
  >;
  private serialize;
  private deserialize;
}
